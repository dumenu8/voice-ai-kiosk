import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KioskService, MenuItem } from '../../services/kiosk';

@Component({
  selector: 'app-menu-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './menu-list.html',
  styleUrl: './menu-list.scss'
})
export class MenuListComponent implements OnInit {
  items = signal<MenuItem[]>([]);
  isLoading = signal<boolean>(true);

  constructor(private kioskService: KioskService) { }

  ngOnInit() {
    this.kioskService.getMenu().subscribe({
      next: (data) => {
        this.items.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.isLoading.set(false);
      }
    });
  }
}
