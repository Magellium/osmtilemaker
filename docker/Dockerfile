FROM postgres:10

###
# Set WORKDIR
###

ARG INSTALLWORKDIR
RUN mkdir $INSTALLWORKDIR
WORKDIR $INSTALLWORKDIR

###
# Environment variables
###

ENV POSTGIS_VERSION 2.5
ENV OSM2PGSQL_VERSION 1.2.0

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
    libmapnik-dev \
    python-mapnik \
    mapnik-utils \
    # fonts
    fontconfig \
    ttf-unifont \
    fonts-noto-cjk \
    fonts-noto-hinted \
    fonts-noto-unhinted \
    # then clean
    && rm -rf /var/lib/apt/lists/*

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

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
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
    git clone https://github.com/gravitystorm/openstreetmap-carto

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


        