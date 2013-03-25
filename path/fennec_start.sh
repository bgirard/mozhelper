
adb shell am start -n org.mozilla.fennec_$USER/.App -d $1 --es env0 NSPR_LOG_MODULES=layers:9 --es env1 MOZ_GL_DEBUG=true --es env2 MOZ_CRASHREPORTER=1
log.sh | grep BenDebug
