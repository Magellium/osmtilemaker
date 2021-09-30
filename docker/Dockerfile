FROM postgres:13-bullseye

###
# Set WORKDIR
###

ARG INSTALLWORKDIR
RUN mkdir $INSTALLWORKDIR
WORKDIR $INSTALLWORKDIR

###
# Environment variables
###

ENV POSTGIS_VERSION 3
ENV OSM2PGSQL_VERSION 1.5.1
ENV OPENSTREETMAP_CARTO_VERSION 5.4.0
ENV MAPNIK_VERSION 3.1
ENV NODEJS_VERSION 16.x
ENV PSYCOPG2_VERSION 2.9.1

###
# Install dependencies
###

RUN \
    apt-get update && apt-get install -y --no-install-recommends \
    # utils
    git \
    software-properties-common \
    sudo \
    wget \ 
    unzip \
    curl \
    # osm2pgsql
    make cmake g++ libboost-dev libboost-system-dev \
    libboost-filesystem-dev libexpat1-dev zlib1g-dev \
    libbz2-dev libpq-dev libproj-dev lua5.2 liblua5.2-dev \
    # postgis
    postgresql-${PG_MAJOR}-postgis-${POSTGIS_VERSION} \
    postgresql-${PG_MAJOR}-postgis-${POSTGIS_VERSION}-scripts \
    # mapnik
    libboost-all-dev \
    libmapnik${MAPNIK_VERSION} \
    python3-mapnik \
    mapnik-utils \
    # openstreetmap-carto
    python3-pip \
    python3-setuptools \
    gdal-bin \
    # fonts
    fontconfig \
    ttf-unifont \
    fonts-noto-cjk \
    fonts-noto-hinted \
    fonts-noto-unhinted \
    # then clean
    && rm -rf /var/lib/apt/lists/*

# openstreetmap-carto python libraries
RUN \
    pip3 install pyyaml requests wheel && \
    pip3 install -Iv psycopg2==${PSYCOPG2_VERSION}

###
# Install osm2pgsql
###

RUN wget https://github.com/openstreetmap/osm2pgsql/archive/${OSM2PGSQL_VERSION}.zip && \
    unzip ${OSM2PGSQL_VERSION}.zip && rm ${OSM2PGSQL_VERSION}.zip &&\
    cd osm2pgsql-${OSM2PGSQL_VERSION} && mkdir build && cd build && \
    cmake .. && make && make install

###
# Install carto
###

RUN curl -sL https://deb.nodesource.com/setup_${NODEJS_VERSION} | bash - && \
    apt-get install -y --no-install-recommends \
    nodejs \
    # then clean
    && rm -rf /var/lib/apt/lists/*

RUN npm -g install carto

###
# Grab some extra noto fonts from Google
###

RUN \
    mkdir -p noto && \
    wget https://noto-website-2.storage.googleapis.com/pkgs/Noto-hinted.zip -q -O noto/Noto-hinted.zip && \
    unzip noto/Noto-hinted.zip -d noto && \
    mv noto/*.otf /usr/share/fonts/opentype/noto && \
    mv noto/*.ttf /usr/share/fonts/truetype/noto && \
    rm -r noto
    
RUN fc-cache

###
# Clone openstreetmap-carto repository
###

RUN \
    git clone https://github.com/gravitystorm/openstreetmap-carto && \
    cd openstreetmap-carto && \
    git checkout v${OPENSTREETMAP_CARTO_VERSION}

###
# Clean
###

RUN \
    apt-get update && apt-get remove -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        make cmake g++ && \
    apt-get autoremove -y


        
