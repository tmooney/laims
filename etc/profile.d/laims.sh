# laims mgi lsf -*-sh-*-

host=$(hostname)
if [[ "${host}" == *.gsc.wustl.edu ]]; then # @ MGI
    # LSF
    if hash bsub 2> /dev/null; then 
        [ -f /opt/lsf9/conf/profile.lsf ] && . /opt/lsf9/conf/profile.lsf
    fi

    # Set Home
    iam=$(whoami)
    if [ -d "/gscmnt/gc2802/halllab/${iam}" ]; then
        HOME="/gscmnt/gc2802/halllab/${iam}"
    elif [ -d "/gscuser/${iam}" ]; then
        HOME="/gscuser/${iam}"
    fi
    export HOME
    unset iam

fi
unset host
