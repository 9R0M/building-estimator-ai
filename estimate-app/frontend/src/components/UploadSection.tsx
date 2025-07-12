import React from "react";
import styles from "./UploadSection.module.css"; // 必要に応じてパスを修正
type UploadSectionProps = {
 imageLoading: boolean;
 handler: (e: React.FormEvent<HTMLFormElement>) => Promise<void>;
 setSelectedFiles: (files: File[]) => void;
};
export default function UploadSection(props: UploadSectionProps) {
 const { imageLoading, handler, setSelectedFiles } = props;
 const handleImageSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
   const files = e.target.files;
   if (!files || files.length === 0) return;
   const fileArray = Array.from(files);
   setSelectedFiles(fileArray);
 };
 return (
<div className={styles.uploadSection}>
<h3>図面画像から構造・階数・面積を自動抽出</h3>
<div className={styles.uploadInput}>
<form onSubmit={handler}>
<input
           type="file"
           accept="image/*"
           multiple
           onChange={handleImageSelection}
         />
<button type="submit">アップロード</button>
</form>
</div>
     {imageLoading && (
<p className={styles.loadingText}>解析中...</p>
     )}
</div>
 );
}