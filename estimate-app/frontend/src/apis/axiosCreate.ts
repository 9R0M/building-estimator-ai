//estimate-app\frontend\src\apis\axiosCreate.ts
import axios from "axios";
export const axoisApi = axios.create({
 baseURL: import.meta.env.VITE_SERVER_URL,
 headers: {
   "Content-Type": "application/json"

 },
});
