import argparse,json,os,signal,socket,sys,time
from datetime import datetime,timezone
from pathlib import Path
from app.core.settings import get_settings
from app.services.notification_service import NotificationService

LOCK_PORT=47831
stopping=False

def log(level,event,**fields):
 print(json.dumps({"timestamp":datetime.now(timezone.utc).isoformat(),"level":level,"event":event,**fields},separators=(",",":")),flush=True)

def acquire_lock():
 lock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 try:lock.bind(("127.0.0.1",LOCK_PORT));lock.listen(1);return lock
 except OSError:lock.close();return None

def request_shutdown(*_):
 global stopping
 stopping=True
 log("INFO","scanner_shutdown_requested")

def run_once(batch_size=None):
 result=NotificationService.scan_all(batch_size=batch_size)
 log("INFO","notification_scan_complete",properties_scanned=result["properties_scanned"],created=result["created"],updated=result["updated"],resolved=result["resolved"])
 return result

def main(argv=None):
 settings=get_settings();parser=argparse.ArgumentParser(description="Scan CRM records into in-app notifications.");parser.add_argument("--interval",type=int,default=0,help="Repeat every N seconds; omit for hosted cron one-shot.");parser.add_argument("--batch-size",type=int,default=settings.SCANNER_BATCH_SIZE);parser.add_argument("--pid-file");args=parser.parse_args(argv)
 if args.interval<0 or args.batch_size<1:parser.error("interval must be non-negative and batch-size must be positive")
 lock=acquire_lock()
 if not lock:log("ERROR","scanner_overlap_rejected");return 2
 signal.signal(signal.SIGINT,request_shutdown)
 if hasattr(signal,"SIGTERM"):signal.signal(signal.SIGTERM,request_shutdown)
 pid_path=Path(args.pid_file) if args.pid_file else None
 if pid_path:pid_path.write_text(str(os.getpid()),encoding="utf-8")
 exit_code=0
 try:
  while not stopping:
   try:run_once(args.batch_size)
   except Exception as exc:
    log("ERROR","notification_scan_failed",exception_category=type(exc).__name__)
    exit_code=1
    if args.interval<=0:break
   if args.interval<=0:break
   deadline=time.monotonic()+args.interval
   while not stopping and time.monotonic()<deadline:time.sleep(min(0.5,deadline-time.monotonic()))
 finally:
  lock.close()
  if pid_path:
   try:pid_path.unlink(missing_ok=True)
   except OSError:pass
  log("INFO","scanner_stopped",exit_code=exit_code)
 return exit_code
if __name__=="__main__":raise SystemExit(main())
