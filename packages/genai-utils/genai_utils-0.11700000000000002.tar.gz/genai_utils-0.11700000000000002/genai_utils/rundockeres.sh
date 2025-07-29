!/usr/bin/sh
# run . ./rundocker.sh
docker network ls | grep demonet ; if [ "$?" != "0" ]; then docker network create demonet ; fi 
#mkdir ~/data/elastic # on linux mkdir /disk01/elastic

if [ -z "${ESI}" ]; then
    export ESI='-p 9200:9200 -p 9300:9300 docker.elastic.co/elasticsearch/elasticsearch:8.18.1'
fi
if [ -z "${ESP}" ]; then
export ESP='-e ELASTICSEARCH_PASSWORD=elastic -e ELASTICSEARCH_USERNAME=elastic'
fi

if [ -z "${ESS}" ]; then
export ESS='-e xpack.security.enabled=false -e discovery.type=single-node -e network.host=0.0.0.0'
fi

#export ESV='-v ~/data/elastic:/usr/share/elasticsearch/data'
#docker run --rm -it --name es01 --network=demonet ${ESS} ${ESV} ${ESP} ${ESI} 

#for LINUX
docker volume create es
if [ -z "${ESV}" ]; then
    export ESV='--mount source=es,target=/usr/share/elasticsearch/data,type=volume'
fi

if [ -z "${ESI}" ]; then
    echo
    echo "*** ERROR ***"
    echo "ESI is *NOT* defined as: ${ESI+x}"
    echo "ERROR ESI is not defined - run this as ". rundockeres.sh" \n"
    echo
else
    echo "ESI == ${ESI}"
    echo "ESP == ${ESP}"
    echo "ESS == ${ESS}"
    echo "ESV == ${ESV}"
    docker run --rm -itd --name es01 --network=demonet ${ESS} ${ESV} ${ESP} ${ESI} 
fi

# docker exec -it es01 bash 
