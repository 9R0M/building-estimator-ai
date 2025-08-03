//estimate-app\frontend\src\apis\axiosCreate.ts
import axios from "axios";
import { serverUrl } from "../local.env";
export const axoisApi = axios.create({
 baseURL: serverUrl,
 headers: {
   "Content-Type": "application/json"

 },
});
