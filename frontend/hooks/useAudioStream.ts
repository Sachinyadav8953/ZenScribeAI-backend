"use client";

import { useCallback, useRef, useState } from "react";
import Cookies from "js-cookie";
import { Transcript } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

interface UseAudioStreamReturn {
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  transcripts: Transcript[];
  isRecording: boolean;
  isConnected: boolean;
  error: string | null;
  clearTranscripts: () => void;
}

export function useAudioStream(consultationUuid: string): UseAudioStreamReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsRecording(false);
    setIsConnected(false);
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);

    // 1. Get microphone
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
    } catch {
      setError("Microphone permission denied. Please allow microphone access.");
      return;
    }

    // 2. Open WebSocket
    const token = Cookies.get("access_token");
    const wsUrl = `${WS_URL}/audio/stream/${consultationUuid}?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);

      // 3. Start MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          ws.send(e.data);
        }
      };

      recorder.start(250); // send chunks every 250ms
      setIsRecording(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as Transcript;
        setTranscripts((prev) => [...prev, data]);
      } catch {
        // non-JSON message, ignore
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection error. Check if the server is running.");
      stopRecording();
    };

    ws.onclose = (e) => {
      setIsConnected(false);
      if (isRecording) {
        setError("Recording connection lost. Click Start Recording to reconnect.");
        setIsRecording(false);
      }
    };
  }, [consultationUuid, isRecording, stopRecording]);

  const clearTranscripts = useCallback(() => setTranscripts([]), []);

  return {
    startRecording,
    stopRecording,
    transcripts,
    isRecording,
    isConnected,
    error,
    clearTranscripts,
  };
}
