import {useState} from "react";
import {Navigate,useSearchParams} from "react-router-dom";
import {useAuth} from "../context/AuthContext";
import {requestPasswordReset} from "../services/authService";

export default function SignIn(){
  const {session,signIn}=useAuth();
  const [params]=useSearchParams();
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [message,setMessage]=useState("");
  const [busy,setBusy]=useState(false);
  const requested=params.get("next");
  const next=requested?.startsWith("/")&&!requested.startsWith("//")?requested:"/";
  if(session)return <Navigate to={next} replace/>;
  const submit=async()=>{
    setBusy(true);setMessage("");
    try{await signIn(email,password)}
    catch(error){setMessage(error instanceof Error?error.message:"Sign-in failed.")}
    finally{setBusy(false)}
  };
  return <main style={{maxWidth:420,margin:"80px auto",padding:24}}>
    <h1>Sign in</h1>
    <p>Access your organization’s property workspace.</p>
    <label>Email<input type="email" value={email} onChange={event=>setEmail(event.target.value)}/></label>
    <label>Password<input type="password" value={password} onChange={event=>setPassword(event.target.value)}/></label>
    <button disabled={busy||!email||!password} onClick={()=>void submit()}>{busy?"Signing in…":"Sign in"}</button>
    <button disabled={!email} onClick={()=>void requestPasswordReset(email).then(()=>setMessage("Password reset instructions requested."),error=>setMessage(error.message))}>Reset password</button>
    {message&&<p>{message}</p>}
  </main>;
}
