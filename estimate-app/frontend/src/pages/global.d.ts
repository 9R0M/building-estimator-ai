// src/global.d.ts
declare global {
 namespace NodeJS {
   interface ProcessEnv {
     VITE_API_URL: string;
     DEFAULT_LOCALE?: string;
   }
 }
 interface Window {
   myAppConfig?: {
     locale: string;
     version: string;
   };
 }
}
export {};