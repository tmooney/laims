# laims mgi lsf -*-sh-*-

# LSF
[ -f /opt/lsf9/conf/profile.lsf ] && . /opt/lsf9/conf/profile.lsf

# Set Home
iam=$(whoami)
if [ -d "/gscmnt/gc2802/halllab/${iam}" ]; then
    HOME="/gscmnt/gc2802/halllab/${iam}"
elif [ -d "/gscuser/${iam}" ]; then
    HOME="/gscuser/${iam}"
fi
export HOME
unset iam
