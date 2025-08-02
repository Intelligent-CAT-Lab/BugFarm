FROM ubuntu:22.04

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Java versions
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    curl \
    git \
    python3-pip \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Install OpenJDK 8 and OpenJDK 11
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    openjdk-11-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Install Maven 3.6.3 (specific version for compatibility)
RUN wget https://archive.apache.org/dist/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz -P /tmp \
    && tar xf /tmp/apache-maven-3.6.3-bin.tar.gz -C /opt \
    && ln -s /opt/apache-maven-3.6.3 /opt/maven \
    && rm /tmp/apache-maven-3.6.3-bin.tar.gz

# Set Maven environment variables
ENV M2_HOME=/opt/maven
ENV MAVEN_HOME=/opt/maven
ENV PATH=${M2_HOME}/bin:${PATH}

# Configure Java environment and alternatives
RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java 1080 \
    && update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-11-openjdk-amd64/bin/java 1100 \
    && update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac 1080 \
    && update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-11-openjdk-amd64/bin/javac 1100
    
# Set up JAVA_HOME environment variables for both versions
ENV JAVA_8_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV JAVA_11_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Add helper scripts to switch between Java versions easily
RUN echo '#!/bin/bash\nupdate-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java\nupdate-alternatives --set javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac\nexport JAVA_HOME=$JAVA_8_HOME' > /usr/local/bin/use_java8 \
    && echo '#!/bin/bash\nupdate-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java\nupdate-alternatives --set javac /usr/lib/jvm/java-11-openjdk-amd64/bin/javac\nexport JAVA_HOME=$JAVA_11_HOME' > /usr/local/bin/use_java11 \
    && chmod +x /usr/local/bin/use_java8 \
    && chmod +x /usr/local/bin/use_java11

# Start with Java 11 as default
RUN update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java \
    && update-alternatives --set javac /usr/lib/jvm/java-11-openjdk-amd64/bin/javac

# Install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh

# Add conda to path
ENV PATH=/opt/conda/bin:$PATH

# Copy environment.yaml and set up the environment
WORKDIR /app
COPY environment.yaml .
RUN conda env create -f environment.yaml

# Create a script to activate conda environment automatically
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate bugfarm" > ~/.bashrc

# Copy setup.sh first to leverage Docker cache
COPY setup.sh /app/

# Run the setup script to install dependencies
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate bugfarm && \
    chmod +x /app/setup.sh && \
    SKIP_PROJECTS=true /app/setup.sh"

# Copy remaining project files
COPY . /app

# Create directories needed for the project
RUN mkdir -p /app/projects /app/logs /app/data

# Add entry script that runs setup.sh for projects when container starts
RUN echo '#!/bin/bash\n\n# Verify Maven installation\nmvn --version\n\n# Verify Java installations\necho "Java 8 installation:"\n$JAVA_8_HOME/bin/java -version\necho "Java 11 installation:"\n$JAVA_11_HOME/bin/java -version\n\n# Check if projects need to be downloaded\nif [ ! -d "/app/projects/commons-cli" ]; then\n  echo "Projects not found, downloading..."\n  bash /app/setup.sh\nfi\n\nexec "$@"' > /app/docker-entrypoint.sh \
    && chmod +x /app/docker-entrypoint.sh

# Create projects directory (for the setup.sh script to download into)
RUN mkdir -p /app/projects

# Expose ports if needed for any web services
# EXPOSE 8000

# Use entrypoint script to ensure projects are downloaded
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Set default command to bash with conda environment activated
CMD ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate bugfarm && /bin/bash"]