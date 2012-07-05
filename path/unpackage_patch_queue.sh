filename=$(basename "$1")
extension="${filename##*.}"
filename="${filename%.*}"
queue_name="${filename#patches-}"

echo "Import $1 to patch queue $filename"

[ -d ".hg" ] || {
  echo "Not at the root of your hg directory"
  exit
}

[ -e "$1" ] || {
  echo "$1 does not exist"
  exit
}

[ -d ".hg/$filename" ] && {
  echo ".hg/$filename already exists"
  exit
}

mkdir ".hg/$filename" && tar -C ".hg/$filename" -xvf "$1" && echo "$queue_name" >> .hg/patches.queues

echo "Create queue $queue_name"

