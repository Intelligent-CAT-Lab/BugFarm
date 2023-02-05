function install_requirements() {
    ansi==0.3.6;
    git+https://github.com/jose/javalang.git@start_position_and_end_position;
    matplotlib==3.3.4;
    nltk==3.6.7
    numpy==1.21.6
    seaborn==0.12.2
    torch==1.12.1
    transformers==4.22.2
    wordninja==2.0.0
}

function download_projects() {
    mkdir -p projects;
    git clone https://github.com/apache/commons-cli projects/commons-cli;
    git clone https://github.com/jfree/jfreechart projects/jfreechart;
    git clone https://github.com/apache/commons-codec projects/commons-codec;
    git clone https://github.com/apache/commons-collections projects/commons-collections;
    git clone https://github.com/apache/commons-compress projects/commons-compress;
    git clone https://github.com/apache/commons-csv projects/commons-csv;
    git clone https://github.com/google/gson projects/gson;
    git clone https://github.com/apache/commons-lang projects/commons-lang;
    git clone https://github.com/apache/commons-math projects/commons-math;
    git clone https://github.com/apache/commons-jxpath projects/commons-jxpath;
    git clone https://github.com/FasterXML/jackson-dataformat-xml projects/jackson-dataformat-xml;
    git clone https://github.com/FasterXML/jackson-core projects/jackson-core;
    git clone https://github.com/FasterXML/jackson-databind projects/jackson-databind;
    git clone https://github.com/jhy/jsoup projects/jsoup;
    git clone https://github.com/JodaOrg/joda-time projects/joda-time;
    git clone https://github.com/mockito/mockito projects/mockito;
}

install_requirements;
download_projects;
