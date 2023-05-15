# vim: set ft=bash ts=3 sw=3 expandtab:
# Build release artifacts into the dist/ directory

command_poetrypublish() {
   echo "Pushing release to fury.io ..."

   env>/tmp/f2
   package=$(poetry version|cut -d " " -f 1)
   poetry publish --repository fury-pub
   if [ $? != 0 ]; then
      echo "*** Publish failed"
      exit 1
   fi
   
   private_count=$(fury list|grep -c private)
   if [ $private_count -gt 1 ] ; then
      highlight "More than 1 private packages - ^please fix"
      fury list
   else
      fury versions $package
   fi




   echo "done"
}

