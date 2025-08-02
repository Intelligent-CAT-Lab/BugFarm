function install_requirements() {
    echo "=== Installing Python requirements ==="
    pip3 install ansi==0.3.6
    pip3 install git+https://github.com/jose/javalang.git@start_position_and_end_position
    pip3 install matplotlib==3.3.4
    pip3 install nltk==3.6.7
    pip3 install numpy==1.21.6
    pip3 install seaborn==0.12.2
    pip3 install torch==1.12.1
    pip3 install transformers==4.22.2
    pip3 install wordninja==2.0.0
    
    echo "=== Setting up tokenizer tool ==="
    if [ ! -d "source-code-tokenizer" ]; then
        git clone https://github.com/devreplay/source-code-tokenizer.git
        cd source-code-tokenizer
        pip install -e .
        cd ..
    else
        echo "Tokenizer tool already exists."
    fi
    
    echo "Requirements installation completed."
}

function download_projects() {
    echo "=== Downloading benchmark projects ==="
    mkdir -p projects
    main=`pwd`
    
    # Project details with names for better tracking
    declare -A projects=(
        ["commons-cli"]="https://github.com/apache/commons-cli b18139a6d1a48bdc19239454c8271ded8184c68a"
        ["jfreechart"]="https://github.com/jfree/jfreechart e2d6788d594c51941ddae337ae666fda5c52ad9f"
        ["commons-codec"]="https://github.com/apache/commons-codec 2eddb17292ea79a6734bc9b0c447ac6d9da0af53"
        ["commons-collections"]="https://github.com/apache/commons-collections 1f297c969c774a97bf72bc710c5e1e8a3e039f79"
        ["commons-compress"]="https://github.com/apache/commons-compress e6930d06cfebbdbee586b863481779b2c4b9b202"
        ["commons-csv"]="https://github.com/apache/commons-csv 420cd15cac9be508930570cb48eee63e25ad5d78"
        ["gson"]="https://github.com/google/gson 19f54ee6ed33b7517c729c801bc57c8c0478be7d"
        ["commons-lang"]="https://github.com/apache/commons-lang eaff7e0a693455081932b53688029f0700447305"
        ["commons-math"]="https://github.com/apache/commons-math 889d27b5d7b23eaf1ee984e93b892b5128afc454"
        ["commons-jxpath"]="https://github.com/apache/commons-jxpath db457cfd3a0cb45a61030ab2d728e080035baef6"
        ["jackson-dataformat-xml"]="https://github.com/FasterXML/jackson-dataformat-xml 0e59be67bd3e9cfcd73b2b62a95bcc0f5b2dda3c"
        ["jackson-core"]="https://github.com/FasterXML/jackson-core 5956b59a77f9599317c7ca7eaa073cb5d5348940"
        ["jackson-databind"]="https://github.com/FasterXML/jackson-databind 1c3c3d87380f7c7a961e169f3bd6bfeb877b89a6"
        ["jsoup"]="https://github.com/jhy/jsoup e52224fbfe6632248cc58c593efae9a22ba2e622"
        ["joda-time"]="https://github.com/JodaOrg/joda-time 0440038eabedcebc96dded95d836e0e1d576ee25"
    )
    
    total=${#projects[@]}
    current=0
    
    for project_name in "${!projects[@]}"; do
        current=$((current + 1))
        read -r repo_url commit_hash <<< "${projects[$project_name]}"
        
        echo "[$current/$total] Processing $project_name"
        
        if [ -d "projects/$project_name" ]; then
            echo "  Project directory exists, checking commit..."
            cd "projects/$project_name"
            current_hash=$(git rev-parse HEAD)
            if [ "$current_hash" = "$commit_hash" ]; then
                echo "  Already at correct commit $commit_hash"
                cd "$main"
                continue
            fi
            cd "$main"
        fi
        
        echo "  Cloning $repo_url to projects/$project_name"
        git clone "$repo_url" "projects/$project_name" || {
            echo "  ERROR: Failed to clone $project_name, continuing with next project"
            continue
        }
        
        cd "projects/$project_name"
        echo "  Setting commit to $commit_hash"
        git reset --hard "$commit_hash" || echo "  WARNING: Could not reset to specific commit"
        cd "$main"
    done
    
    echo "Project download completed."
}

function build_projects {
    echo "=== Building projects ==="
    main=`pwd`
    
    # Projects that need Java 8 specifically
    java8_projects=("commons-lang" "joda-time")
    
    # Get all project directories
    projects_dirs=($(ls -d projects/*))
    total=${#projects_dirs[@]}
    current=0
    
    for project_path in "${projects_dirs[@]}"; do
        project_name=$(basename "$project_path")
        current=$((current + 1))
        
        if [ ! -f "$project_path/pom.xml" ]; then
            echo "[$current/$total] Skipping $project_name (no pom.xml found)"
            continue
        fi
        
        echo "[$current/$total] Building $project_name"
        cd "$project_path"
        
        # Check if this project needs Java 8
        if [[ " ${java8_projects[*]} " == *" $project_name "* ]]; then
            echo "  Using Java 8 for this project"
            # Check if we're in Docker or local environment
            if [ -f "/usr/local/bin/use_java8" ]; then
                # In Docker, use helper scripts
                source /usr/local/bin/use_java8
                mvn test --log-file build.log
                source /usr/local/bin/use_java11
            elif command -v update-alternatives > /dev/null; then
                # Fallback to direct update-alternatives if helper scripts not available
                update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
                mvn test --log-file build.log
                update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java
            else
                # On macOS, use /usr/libexec/java_home
                JAVA_HOME=`/usr/libexec/java_home -v 1.8` mvn test --log-file build.log
            fi
        else
            echo "  Using default Java version"
            mvn test --log-file build.log
        fi
        
        build_status=$?
        if [ $build_status -eq 0 ]; then
            echo "  Build successful"
        else
            echo "  Build failed with status $build_status"
        fi
        
        cd "$main"
    done
    
    echo "Project builds completed."
}

# Create directories for logs and data
mkdir -p logs
mkdir -p data

# Main execution flow with error handling
echo "=== Starting BugFarm setup $(date) ==="

install_requirements || { echo "Failed to install requirements"; exit 1; }

# Skip downloading and building projects if SKIP_PROJECTS is set (for Docker build)
if [ "$SKIP_PROJECTS" != "true" ]; then
  download_projects || { echo "Failed to download projects"; exit 1; }
  build_projects || { echo "Failed to build projects"; exit 1; }
else
  echo "Skipping project download and build (SKIP_PROJECTS=true)"
fi

echo "=== BugFarm setup completed successfully $(date) ==="
