#!/usr/bin/env python3
import fnmatch, hashlib, io, json, os, pathlib, sys, tarfile
args=sys.argv[1:]
image_config=b'{"architecture":"amd64","os":"linux","rootfs":{"type":"layers","diff_ids":[]}}'
image_id="sha256:"+hashlib.sha256(image_config).hexdigest()
if args and args[0]=="ps":
    if os.environ.get("FAIL_DOCKER_PS")=="1":sys.exit(37)
    print(os.environ.get("RUNNING_CONTAINERS",""))
    sys.exit(0)
if args[:2]==["volume","inspect"]:sys.exit(1)
if args and args[0]=="inspect":
    if os.environ.get("FAIL_RUNTIME_CAPTURE")=="1":sys.exit(31)
    print(json.dumps([{"Image":image_id, "Config":{"Image":"fixture/image:1","Env":["FIXTURE_SECRET=not-a-real-secret"],"User":"1000:1000"},"Mounts":[]}]))
    sys.exit(0)
if args[:2]==["image","inspect"]:
    if os.environ.get("FAIL_IMAGE_INSPECT")=="1":sys.exit(38)
    print(json.dumps([{"RepoDigests":["fixture/image@sha256:fixture"]}]))
    sys.exit(0)
if args[:2]==["image","save"]:
    if os.environ.get("FAIL_LOCAL_IMAGE")=="1":sys.exit(39)
    manifest=json.dumps([{"Config":"config.json","Layers":[]}]).encode()
    with tarfile.open(args[args.index("--output")+1],"w") as archive:
        for name,content in [("manifest.json",manifest),("config.json",image_config)]:
            member=tarfile.TarInfo(name);member.size=len(content);archive.addfile(member,io.BytesIO(content))
    sys.exit(0)
if args[:2]==["exec","traefik"]:
    if os.environ.get("FAIL_PLUGIN_EXPORT")=="1":sys.exit(33)
    source=pathlib.Path(os.environ["FIXTURE_TRAEFIK_PLUGINS"])
elif args[:2]==["exec","crowdsec"]:
    if os.environ.get("FAIL_CROWDSEC")=="1":sys.exit(19)
    source=pathlib.Path(os.environ["FIXTURE_CROWDSEC"])
elif args and args[0]=="run":
    assert "--read-only" in args and "--pull=never" in args
    assert args[args.index("--network")+1]=="none"
    mounts=[args[n+1] for n,value in enumerate(args) if value=="--mount"]
    assert all(mount.endswith(",readonly") for mount in mounts)
    if len(mounts)>1:
        if os.environ.get("FAIL_HOST_EXPORT")=="1":sys.exit(32)
        actual={next(part.split("=",1)[1] for part in mount.split(",") if part.startswith("source=")) for mount in mounts}
        expected={"/root/.config/olm-client/config.json","/etc/systemd/system/olm.service","/etc/systemd/system/arr-mcp-tunnel.service","/etc/systemd/system/olm-watchdog.service","/etc/systemd/system/olm-watchdog.timer","/usr/local/sbin/olm-watchdog.sh","/usr/local/sbin/homarr-appdata-tar","/etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml","/etc/systemd/system/crowdsec-firewall-bouncer.service"}
        assert actual==expected
        source=pathlib.Path(os.environ["FIXTURE_HOST_RECOVERY"])
    else:
        source=pathlib.Path(next(part.split("=",1)[1] for part in mounts[0].split(",") if part.startswith("source=")))
    if source.name=="data" and os.environ.get("FAIL_PRIVATE_EXPORT")=="1":sys.exit(23)
else:sys.exit(99)
patterns=[arg.split("=",1)[1] for arg in args if arg.startswith("--exclude=")]
def keep(member):
    return None if any(fnmatch.fnmatch(member.name,pattern) for pattern in patterns) else member
with tarfile.open(mode="w|",fileobj=sys.stdout.buffer) as stream:
    stream.add(source,arcname=".",filter=keep)
    if source.name=="data":
        content=b"recovery journal captured by an earlier raw copy"
        member=tarfile.TarInfo("./pocket-id/pocket-id.db-journal");member.size=len(content)
        stream.addfile(member,io.BytesIO(content))
