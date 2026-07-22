import argparse,os,socket,sys,time
from pathlib import Path
from app.core.settings import get_settings
from app.services.notification_service import NotificationService

LOCK_PORT=47831
def acquire_lock():
 lock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 try:lock.bind(("127.0.0.1",LOCK_PORT));lock.listen(1);return lock
 except OSError:lock.close();return None
def run_once():
 result=NotificationService.scan_all();print(f"Notification scan complete: properties={result['properties_scanned']} created={result['created']} updated={result['updated']} resolved={result['resolved']}",flush=True);return result
def main(argv=None):
 parser=argparse.ArgumentParser(description="Scan CRM records into in-app notifications.");parser.add_argument("--interval",type=int,default=0,help="Repeat every N seconds; omit for one scan.");parser.add_argument("--pid-file");args=parser.parse_args(argv)
 lock=acquire_lock()
 if not lock:print("Notification scanner is already running; exiting.",file=sys.stderr);return 2
 pid_path=Path(args.pid_file) if args.pid_file else None
 if pid_path:pid_path.write_text(str(os.getpid()),encoding="utf-8")
 try:
  while True:
   try:run_once()
   except Exception as exc:print(f"Notification scan failed: {exc}",file=sys.stderr,flush=True)
   if args.interval<=0:break
   time.sleep(args.interval)
 finally:
  lock.close()
  if pid_path:
   try:pid_path.unlink(missing_ok=True)
   except OSError:pass
 return 0
if __name__=="__main__":raise SystemExit(main())
