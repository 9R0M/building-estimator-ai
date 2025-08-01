// src/components/UploadSection.tsx
import React, { useEffect } from 'react';
import { toast } from 'react-toastify';
import styles from '../styles/UploadSection.module.css';

export type FileWithPreview = File & { preview: string };

interface Props {
    files: FileWithPreview[];
    setFiles: (updater: (prev: FileWithPreview[]) => FileWithPreview[]) => void;
}

const MAX_FILES = 10;

const UploadSection: React.FC<Props> = ({ files, setFiles }) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files) return;
        const selected = Array.from(e.target.files)
            .filter(f => f.type.startsWith('image/'))
            .map(f => Object.assign(f, { preview: URL.createObjectURL(f) }));

        setFiles(prev => {
            const combined = [...prev, ...selected];
            if (combined.length > MAX_FILES) {
                toast.warning(`画像は最大${MAX_FILES}枚までです`);
            }
            return combined.slice(0, MAX_FILES);
        });

        e.target.value = ''; // 同一ファイルの再選択を可能にする
    };

    const handleRemove = (idx: number) => {
        setFiles(prev => {
            const next = [...prev];
            URL.revokeObjectURL(next[idx].preview); // 削除時にURL解放
            next.splice(idx, 1);
            return next;
        });
    };

    /* 一旦残す
    const onFilesChange = (selected: File[]) => {
        setFiles((prev) => {
            const newOnes = selected
                .filter(f => f.type.startsWith("image/"))
                .filter(f => !prev.some(p => p.name === f.name && p.size === f.size))
                .slice(0, MAX_FILES - prev.length)
                .map(f => Object.assign(f, { preview: URL.createObjectURL(f) }));
            if (newOnes.length === 0 && prev.length >= MAX_FILES) {
                toast.warning(`画像は最大${MAX_FILES}枚までです`);
            }
            return [...prev, ...newOnes].slice(0, MAX_FILES);
        });
    };
    */

    useEffect(() => {
        return () => {
            // filesが更新（追加・削除）されるたび、
            // 古いプレビューURLをクリーンアップして、現在選択中の10枚だけを保持します
            files.forEach(f => URL.revokeObjectURL(f.preview));
        };
    }, [files]); // → Reactがファイル変更直後に以前のURLを解放するよう保証します  [oai_citation_attribution:0‡Stack Overflow](https://stackoverflow.com/questions/76643347/what-is-the-proper-way-to-create-and-revoke-a-blob-in-react-useeffect?utm_source=chatgpt.com)

    return (
        <div className={styles.uploadSection}>
            <label className={styles.fileInputLabel}>
                画像を選択（最大{MAX_FILES}枚）
                <input
                    className={styles.hiddenFileInput}
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleChange}
                />
            </label>

            <div
                className={styles.previews}
                aria-live="polite"
                aria-atomic="true"
            >
                {files.map((f, i) => (
                    <figure key={i} className={styles.previewItem}>
                        <img src={f.preview} alt={`選択画像 ${i + 1}`} />
                        <button
                            type="button"
                            aria-label={`画像 ${i + 1} を削除`}
                            onClick={() => handleRemove(i)}
                        >
                            ×
                        </button>
                    </figure>
                ))}
            </div>
        </div>
    );
};

export default UploadSection;