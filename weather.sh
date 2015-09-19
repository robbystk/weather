#! /bin/bash

function location_from_homedir()
{
    if [[ -f ~/.location ]]
    then
        . ~/.location
    else
        echo "no location file in home directory" >&2
        exit 1
    fi
}

function location_from_file()
{
    if [[ -f $location_file ]]
    then
        . $location_file
    else
        echo "file $location_file not found" >&2
        location_from_homedir
    fi
}

case $# in
    0 )
        # not given location file
        location_from_homedir
    ;;
    1 )
        # given location file
        location_file=$1
        location_from_file

    ;;
    * )
        # wrong number of arguments
        echo "Usage: $0 [location file]" >&2
        exit 2
    ;;
esac

echo "lat=${lat}&lon=${lon}"
