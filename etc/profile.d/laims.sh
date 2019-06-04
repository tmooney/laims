# laims mgi lsf -*-sh-*-

# Set Home
iam=$(whoami)
if [ -d "/gscmnt/gc2802/halllab/${iam}" ]; then
    HOME="/gscmnt/gc2802/halllab/${iam}"
elif [ -d "/gscuser/${iam}" ]; then
    HOME="/gscuser/${iam}"
else
    HOME="/home/${iam}"
fi
export HOME
unset iam
