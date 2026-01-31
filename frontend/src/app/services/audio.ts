import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  isRecording = signal<boolean>(false);

  async startRecording(): Promise<void> {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.start();
        this.isRecording.set(true);
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    } else {
      console.error('MediaDevices API not supported.');
    }
  }

  stopRecording(): Promise<Blob> {
    return new Promise((resolve) => {
      if (this.mediaRecorder) {
        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' }); // or audio/webm
          this.audioChunks = [];
          this.isRecording.set(false);
          resolve(audioBlob);
        };
        this.mediaRecorder.stop();

        // Stop all tracks to release mic
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      } else {
        resolve(new Blob());
      }
    });
  }

  playAudioBlob(base64Audio: string) {
    const audioSrc = `data:audio/wav;base64,${base64Audio}`;
    const audio = new Audio(audioSrc);
    audio.play().catch(e => console.error("Error playing audio:", e));
  }
}
