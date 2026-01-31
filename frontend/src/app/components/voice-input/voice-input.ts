import { Component, EventEmitter, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AudioService } from '../../services/audio';

@Component({
  selector: 'app-voice-input',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './voice-input.html',
  styleUrl: './voice-input.scss'
})
export class VoiceInputComponent {
  @Output() audioRecorded = new EventEmitter<Blob>();
  isRecording;

  constructor(private audioService: AudioService) {
    this.isRecording = this.audioService.isRecording;
  }

  async startRecording(event?: Event) {
    if (event) {
      event.preventDefault(); // Prevent ghost clicks
    }
    if (!this.isRecording()) {
      await this.audioService.startRecording();
    }
  }

  async stopRecording(event?: Event) {
    if (event) {
      event.preventDefault();
    }
    if (this.isRecording()) {
      const blob = await this.audioService.stopRecording();
      if (blob.size > 0) {
        this.audioRecorded.emit(blob);
      }
    }
  }
}
