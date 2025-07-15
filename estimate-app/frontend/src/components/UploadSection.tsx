// src/components/UploadSection.tsx
import React, { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import styles from "../styles/UploadSection.module.css";
interface UploadSectionProps {
    files: File[];
    setFiles: React.Dispatch<React.SetStateAction<File[]>>;
    onFileRemove?: (index: number) => void;
}
const UploadSection: React.FC<UploadSectionProps> = ({ files, setFiles, onFileRemove }) => {
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef<HTMLInputElement | null>(null);
    const handleFiles = (fileList: FileList | null) => {
        if (!fileList) return;
        const newFiles = Array.from(fileList).filter(
            f => !files.some(existing => existing.name === f.name && existing.size === f.size)
        );
        if (newFiles.length) {
            setFiles(prev => [...prev, ...newFiles]);
        }
    };
    const handleChange = (e: ChangeEvent<HTMLInputElement>) =>
        handleFiles(e.target.files);
    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(true);
    };
    const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
    };
    const handleDrop = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        handleFiles(e.dataTransfer.files);
    };
    const removeFile = (i: number) => {
        setFiles(prev => prev.filter((_, idx) => idx !== i));
        onFileRemove?.(i);
    };
    return (
        <div
            className={`${styles.dropZone} ${dragActive ? styles.active : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={e => {
                if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
            aria-label="ファイルアップロードゾーン。クリックまたはドラッグ＆ドロップでファイルを選択してください。"
        >
            <input
                ref={inputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleChange}
                hidden
            />
            <p>{dragActive ? "ここにファイルをドロップしてください" : "クリックまたはドラッグしてファイルを追加"}</p>
            <div className={styles.preview}>
                {files.map((file, i) => (
                    <div key={i} className={styles.previewItem}>
                        {file.type.startsWith("image/") ? (
                            <img src={URL.createObjectURL(file)} alt={file.name} width={80} />
                        ) : (
                            <div className={styles.fileIcon}>📄</div>
                        )}
                        <div className={styles.fileInfo}>
                            <span title={file.name}>
                                {file.name.length > 20 ? file.name.slice(0, 17) + "..." : file.name}
                            </span>
                            <span>{(file.size / 1024).toFixed(1)} KB</span>
                            <button type="button" onClick={() => removeFile(i)}>
                                削除
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
export default UploadSection;