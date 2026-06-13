import React, { useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CheckCircle2Icon } from "lucide-react";

import { NavigationMenuDemo } from "./menu"
import {RegisterForm} from "./registerform"


import "./App.css";
import { Toaster } from "sonner";

function App() {
  // Type
  type TokenResponse = {
    access_token: string;
    token_type: string;
  };

  const [token, setToken] = useState<TokenResponse | null>(null);
  const [userId, setUserId] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [alarmStatus, setAlarmStatus] = useState<boolean>(false);
  const [alarmMessage, setAlarmMessage] = useState<string>("");
  const [registerPage,setRegisterPage] = useState<boolean>(false)
  const [isLogin, setIsLogin] = useState<boolean>(false)


  const loginRequest = async (
    username: string,
    password: string,
  ): Promise<void> => {
    const body = new URLSearchParams({
      grant_type: "password",
      username: username,
      password: password,
    });
    const res = await fetch("http://localhost:8000/token", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      credentials:"include",
      body: body,
    });

    const data = await res.json();
    if (!res.ok) {
      setAlarmMessage(data.detail);
      setAlarmStatus(true);
    } else {
      setToken(data);
      setIsLogin((prev)=>!prev)
    }
  };

  const login = async (e: React.MouseEvent<HTMLButtonElement>) => {
    if (userId !== "" && password !== "") {
      loginRequest(userId, password);
    } else {
      setAlarmMessage("please type username or pasword");
      setAlarmStatus(true);
    }
  };

  const logout = () => {
    // 토큰 무효화
    setIsLogin((prev)=>!prev)
  }

  const getUsername = async () => {
    const res = await fetch("http://localhost:8000/user/me", {
      method:"GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      credentials:"include",
    })
    const data = await res.json()
    console.log(data.user_id)
    
  }

  return (
    <>
      <div>
        <NavigationMenuDemo isLogin={isLogin}/>
      </div>
      <div>
            
        <Toaster />
        {
        isLogin ?
        
          
        <Card className="w-full max-w-sm ">
          <CardHeader>
            <CardTitle>Hello {}!</CardTitle>
            <CardDescription>
              Welcome
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form>
              <div className="flex flex-col gap-6">
                <Button
                  onClick={getUsername}
                  className="w-full"
                  >
                    유저이름 가지고오기?
                </Button>
              </div>
            </form>
          </CardContent>
          <CardFooter className="flex-col gap-2">
            <Button
              type="submit"
              onClick={logout}
              className="w-full"
              disabled={alarmStatus}
            >
              LogOut
            </Button>
          </CardFooter>
        </Card>
        :
        <Card className="w-full max-w-sm ">
          <CardHeader>
            <CardTitle>Login to your account</CardTitle>
            <CardDescription>
              Enter your ID below to login to your account
            </CardDescription>
            <CardAction>
              <Button variant="link" onClick={()=>{setRegisterPage(!registerPage)}}>Sign Up</Button>
            </CardAction>
          </CardHeader>
          <CardContent>
            <form>
              <div className="flex flex-col gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="email">ID</Label>
                  <Input
                    id="login_email"
                    type="email"
                    placeholder="ID"
                    value={userId}
                    onChange={(e)=>{setUserId(e.target.value);}}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center">
                    <Label htmlFor="password">Password</Label>
                    <a
                      href="#"
                      className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                    >
                      Forgot your password?
                    </a>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e)=>{setPassword(e.target.value);}}
                    required
                  />
                </div>
              </div>
            </form>
          </CardContent>
          <CardFooter className="flex-col gap-2">
            <Button
              type="submit"
              onClick={login}
              className="w-full"
              disabled={alarmStatus}
            >
              Login
            </Button>
            <Button variant="outline" className="w-full">
              Login with Google
            </Button>
          </CardFooter>
        </Card>

}

        {alarmStatus && (
          <div
            className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center select-none"
            onClick={()=>{setAlarmStatus(!alarmStatus);}}
          >
            <Alert className="w-[30%]">
              <CheckCircle2Icon />
              <AlertTitle>Payment successful</AlertTitle>
              <AlertDescription>{alarmMessage}</AlertDescription>
            </Alert>
          </div>
        )}
      </div>
      {registerPage && 
      <div 
        className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center select-none"
        // onClick={()=>{setRegisterPage(!registerPage)}}
      >
        <div 
          className = "w-2xl"
          // onClick={(e)=>e.stopPropagation()}
          >
        <RegisterForm
          registerPage = {registerPage}
          setRegisterPage = {setRegisterPage}
        />
        </div>
      </div>}
    </>
  );
}

export default App;
