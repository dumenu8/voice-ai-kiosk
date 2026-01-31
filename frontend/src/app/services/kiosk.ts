import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
}

export interface OrderItem {
  name: string;
  price: number;
  qty: number;
}

export interface Order {
  id: number;
  session_id: string;
  total_price: number;
  status: string;
  items_json: OrderItem[];
  created_at?: string;
}

export interface ConversationResponse {
  reply_text: string;
  action: string;
  items?: OrderItem[];
  order_id?: number;
  order_status?: string;
  audio_base64?: string;
  user_transcript?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  items?: OrderItem[];
  orderId?: number;
  audioBase64?: string;
}

@Injectable({
  providedIn: 'root'
})
export class KioskService {
  private apiUrl = '/api';
  sessionId = signal<string>(crypto.randomUUID());

  messages = signal<ChatMessage[]>([{
    role: 'assistant',
    content: 'Hi! I am Vivian. What can I get for you today?'
  }]);

  constructor(private http: HttpClient) { }

  resetSession() {
    this.sessionId.set(crypto.randomUUID());
    this.messages.set([{
      role: 'assistant',
      content: 'Hi! I am Vivian. What can I get for you today?'
    }]);
  }

  sendConversation(text?: string, audioBlob?: Blob): Observable<ConversationResponse> {
    const formData = new FormData();
    formData.append('session_id', this.sessionId());

    if (text) {
      formData.append('text', text);
    }

    if (audioBlob) {
      formData.append('audio', audioBlob, 'voice_input.wav');
    }

    return this.http.post<ConversationResponse>(`${this.apiUrl}/conversation`, formData);
  }

  getOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(`${this.apiUrl}/orders`);
  }

  getMenu(): Observable<MenuItem[]> {
    return this.http.get<MenuItem[]>(`${this.apiUrl}/menu`);
  }
}
