#/bin/bash -i
# 
# ${1}: env name
#
ENVS=$(conda env list | awk '{print $1}' )
if [[ $ENVS = *"$1"* ]]; then
   eval "$(conda shell.bash hook)"
   conda activate "${1}"
   conda env export | grep -v "^prefix: " > environment.yml
   conda env export --no-builds | grep -v "^prefix: " > environment-nobuilds.yml

else 
   echo "Error: Please provide a valid virtual environment. Current Conda envs are: "
   conda_envs_=`conda env list`
   printf '%s\n' "$conda_envs_" 
   exit
fi;