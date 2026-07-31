import {useEffect,useState} from "react";
import {Link,useNavigate,useSearchParams} from "react-router-dom";
import {useAuth} from "../context/AuthContext";
import {acceptInvitation} from "../services/authService";

export default function AcceptInvitation(){
  const {session,refreshOrganizations}=useAuth();
  const [params]=useSearchParams();
  const navigate=useNavigate();
  const [message,setMessage]=useState("Validating invitation…");
  const token=params.get("token");
  useEffect(()=>{
    if(!session||!token)return;
    void acceptInvitation(token).then(async()=>{
      await refreshOrganizations();
      setMessage("Invitation accepted. Opening your organization…");
      navigate("/",{replace:true});
    },error=>setMessage(error instanceof Error?error.message:"Invitation could not be accepted."));
  },[session,token,refreshOrganizations,navigate]);
  if(!token)return <main style={{maxWidth:520,margin:"80px auto"}}><h1>Invitation unavailable</h1><p>The invitation link is missing its token.</p></main>;
  if(!session){
    const next=`/invitations/accept?token=${encodeURIComponent(token)}`;
    return <main style={{maxWidth:520,margin:"80px auto"}}><h1>Accept invitation</h1><p>Sign in with the invited account before accepting this organization invitation.</p><Link to={`/sign-in?next=${encodeURIComponent(next)}`}>Sign in to continue</Link></main>;
  }
  return <main style={{maxWidth:520,margin:"80px auto"}}><h1>Accept invitation</h1><p>{message}</p></main>;
}
