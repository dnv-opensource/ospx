REM See http://www.davekuhlman.org/generateds_tutorial.html
REM generateDS -o fmi2_api.py -s fmi2.py --super=fmi2_api fmi2ModelDescription.xsd
generateDS -f -o fmi2_api.py -s fmi2_sub.py --no-dates --no-versions --no-redefine-groups --disable-generatedssuper-lookup --disable-xml --create-mandatory-children fmi2ModelDescription.xsd
