#!/bin/bash
set -e
set -x
SCRIPT_NAME=$0
function usage {
    echo "usage: $SCRIPT_NAME [options] <bucket name> <zip> <fns...>"
    echo "-n update fns without uploading to s3"
    echo "-t to append -test to fn names"
    echo "-d for dry run"
}

if [ "$#" -lt 2 ]
then
    usage
    exit 1
fi

TEST=0
CP=1
DRY=0

for i in 1 2 3
do
    case "$1" in
	-t)
	    TEST=1
	    shift
	    ;;
	-n)
	    CP=0
	    shift
	    ;;
	-d)
	    DRY=1
	    shift
	    ;;
    esac
done

BUCKET=$1
ZIP=$2
shift 2
FNS=$@

if [ -z "$FNS" ]
then
    FNS="authorize consume create createmagiclink dayof-events dayof-slack read reimburse resume send-emails update validate"
fi

#echo "$BUCKET"
#echo "$ZIP"
#echo "$FNS"

if [ "$CP" -eq 1 ]
then
   aws s3 cp $ZIP s3://$BUCKET/$ZIP
fi

for FN in $FNS
do
    if [ "$TEST" -eq 1 ]
    then
	FN="${FN}-test"
    fi

    OPT="--function-name $FN --s3-bucket $BUCKET --s3-key $ZIP"

    if [ "$DRY" -eq 1 ]
    then
	OPT="$OPT --dry-run"
    fi
    
    AWS_DEFAULT_REGION="us-west-2" aws lambda update-function-code $OPT
done
