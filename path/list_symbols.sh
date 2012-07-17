for i in /System/Library/Frameworks/*.framework
do
${var%Pattern}
  name=$( basename $i)
  echo "Framework: ${name%.framework}" 1>&2
  otool -tV $i/${name%.framework}
done

for i in /System/Library/Frameworks/Quartz.framework/Frameworks/*.framework
do
${var%Pattern}
  name=$( basename $i)
  echo "Framework: ${name%.framework}" 1>&2
  otool -tV $i/${name%.framework}
done

find /System/Library/Frameworks/ -name "*.h" | xargs cat

