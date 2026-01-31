import { Routes } from '@angular/router';
import { ChatWindowComponent } from './components/chat-window/chat-window';
import { OrderDashboardComponent } from './components/order-dashboard/order-dashboard';
import { MenuListComponent } from './components/menu-list/menu-list';

export const routes: Routes = [
    { path: 'kiosk', component: ChatWindowComponent },
    { path: 'kitchen', component: OrderDashboardComponent },
    { path: 'menu', component: MenuListComponent },
    { path: '', redirectTo: 'kiosk', pathMatch: 'full' }
];
