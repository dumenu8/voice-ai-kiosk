import { Component, ElementRef, ViewChild, signal, effect, AfterViewChecked, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { KioskService, ConversationResponse, OrderItem, ChatMessage } from '../../services/kiosk';
import { AudioService } from '../../services/audio';
import { VoiceInputComponent } from '../voice-input/voice-input';



@Component({
  selector: 'app-chat-window',
  standalone: true,
  imports: [CommonModule, FormsModule, VoiceInputComponent],
  templateUrl: './chat-window.html',
  styleUrl: './chat-window.scss'
})
export class ChatWindowComponent implements AfterViewChecked {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  private kioskService = inject(KioskService);
  private audioService = inject(AudioService);

  // Accessed via signal from service
  messages = this.kioskService.messages;

  inputText = signal<string>('');
  isLoading = signal<boolean>(false);

  constructor() { }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch (err) { }
  }

  handleVoice(blob: Blob) {
    this.processInput(undefined, blob);
  }

  handleText() {
    if (this.inputText().trim()) {
      this.processInput(this.inputText());
      this.inputText.set('');
    }
  }

  replayAudio(base64: string) {
    this.audioService.playAudioBlob(base64);
  }

  clearChat() {
    this.kioskService.resetSession();
  }

  processInput(text?: string, audio?: Blob) {
    if (!text && !audio) return;

    // Optimistic User Message
    if (text) {
      this.messages.update(msgs => [...msgs, { role: 'user', content: text }]);
    } else {
      this.messages.update(msgs => [...msgs, { role: 'user', content: '🎤 (Audio Input)' }]);
    }

    this.isLoading.set(true);

    this.kioskService.sendConversation(text, audio).subscribe({
      next: (res: ConversationResponse) => {
        this.isLoading.set(false);

        // Update user message if it was audio, replace placeholder
        if (res.user_transcript) {
          this.messages.update(msgs => {
            const newMsgs = [...msgs];
            const lastUserMsgIndex = newMsgs.map(m => m.role).lastIndexOf('user');
            if (lastUserMsgIndex !== -1) {
              newMsgs[lastUserMsgIndex] = { ...newMsgs[lastUserMsgIndex], content: res.user_transcript! };
            }
            return newMsgs;
          });
        }

        const msg: ChatMessage = {
          role: 'assistant',
          content: res.reply_text,
          items: res.items,
          orderId: res.order_id,
          audioBase64: res.audio_base64
        };
        this.messages.update(msgs => [...msgs, msg]);

        if (res.audio_base64) {
          this.audioService.playAudioBlob(res.audio_base64);
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        console.error(err);
        this.messages.update(msgs => [...msgs, { role: 'assistant', content: 'Sorry, I had trouble creating that connection. Please try again.' }]);
      }
    });
  }
}
