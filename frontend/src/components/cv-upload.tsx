"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, LoaderCircle } from "lucide-react";

interface CvUploadProps {
  onFileUpload: (dataUrl: string, file: File) => void;
  isLoading?: boolean;
}

export function CvUpload({ onFileUpload, isLoading = false }: CvUploadProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    if (rejectedFiles.length > 0) {
      setError("Only PDF files are accepted.");
      return;
    }
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target && typeof e.target.result === "string") {
          onFileUpload(e.target.result, selectedFile);
        }
      };
      reader.readAsDataURL(selectedFile);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
    disabled: isLoading,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`w-full p-6 border-2 border-dashed rounded-lg text-center transition-colors
        ${isDragActive ? "border-primary bg-primary/10" : "border-border"}
        ${isLoading ? 'cursor-not-allowed bg-muted/50' : 'cursor-pointer hover:border-primary/50'}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4">
          {isLoading ? (
            <LoaderCircle className="h-12 w-12 text-muted-foreground animate-spin" />
          ) : (
            <UploadCloud className="w-12 h-12 text-muted-foreground" />
          )}

          {isDragActive ? (
            <p className="text-primary">Drop the CV here...</p>
          ) : (
            <div>
              <p className="font-semibold">Drag & drop a CV here, or click to select</p>
              <p className="text-sm text-muted-foreground">PDF format only</p>
            </div>
          )}
        </div>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {isLoading && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <p className="text-sm font-medium text-muted-foreground">Analyzing candidate... this may take a moment.</p>
        </div>
      )}
    </div>
  );
}
