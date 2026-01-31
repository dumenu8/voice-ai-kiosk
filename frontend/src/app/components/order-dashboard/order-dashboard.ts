import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KioskService, Order } from '../../services/kiosk';

@Component({
  selector: 'app-order-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './order-dashboard.html',
  styleUrl: './order-dashboard.scss'
})
export class OrderDashboardComponent implements OnInit {
  orders = signal<Order[]>([]);

  constructor(private kioskService: KioskService) { }

  ngOnInit() {
    this.refreshOrders();
    // Auto-refresh every 5 seconds
    setInterval(() => this.refreshOrders(), 5000);
  }

  refreshOrders() {
    this.kioskService.getOrders().subscribe({
      next: (data) => {
        // Sort by ID desc
        this.orders.set(data.sort((a, b) => b.id - a.id));
      },
      error: (err) => console.error(err)
    });
  }

  formatItems(items: any[]): string {
    if (!items) return '';
    return items.map(i => `${i.qty}x ${i.name}`).join(', ');
  }
}
