// src/api.ts
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",   
  },
});
export const getStatus   = (id:string)=>api.get(`/onboard/status/${id}/`);
export const preRegister = (p:any)=>api.post("/onboard/pre_register/",p);
export const getProfile  = (id:string)=>api.get(`/profile/${id}/`);
