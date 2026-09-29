import Dashboard from '../views/Dashboard.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import AdminTreks from '../views/admin/Treks.vue'
import AdminStaff from '../views/admin/Staff.vue'
import AdminUsers from '../views/admin/Users.vue'
import AdminBookings from '../views/admin/Bookings.vue'
import AdminReports from '../views/admin/Reports.vue'
import StaffTreks from '../views/staff/Treks.vue'
import StaffParticipants from '../views/staff/Participants.vue'
import TrekkerTreks from '../views/trekker/Treks.vue'
import TrekkerBookings from '../views/trekker/Bookings.vue'
import TrekkerHistory from '../views/trekker/History.vue'
import TrekkerProfile from '../views/trekker/Profile.vue'

export const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/admin/treks', component: AdminTreks, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/admin/staff', component: AdminStaff, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/admin/users', component: AdminUsers, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/admin/bookings', component: AdminBookings, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/admin/reports', component: AdminReports, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/staff/treks', component: StaffTreks, meta: { requiresAuth: true, role: 'STAFF' } },
  { path: '/staff/participants/:id', component: StaffParticipants, meta: { requiresAuth: true, role: 'STAFF' } },
  { path: '/trekker/treks', component: TrekkerTreks, meta: { requiresAuth: true, role: 'TREKKER' } },
  { path: '/trekker/bookings', component: TrekkerBookings, meta: { requiresAuth: true, role: 'TREKKER' } },
  { path: '/trekker/history', component: TrekkerHistory, meta: { requiresAuth: true, role: 'TREKKER' } },
  { path: '/trekker/profile', component: TrekkerProfile, meta: { requiresAuth: true, role: 'TREKKER' } }
]
