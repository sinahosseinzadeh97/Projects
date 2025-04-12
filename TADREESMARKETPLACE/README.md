# Tadrees Marketplace

![Tadrees Marketplace](public/screenshots/home-page.png)

## 📚 Overview

Tadrees Marketplace is a comprehensive peer-to-peer tutoring platform that connects students with qualified tutors. This full-stack application enables students to find tutors based on subject expertise, pricing, and availability, while providing tutors with tools to showcase their skills and manage their sessions.

**Created by:** SinaMohammadhHosseinZadeh

## ✨ Features

### For Students
- 🔍 Search and filter tutors by subject, price range, and availability
- 📅 Book and manage tutoring sessions
- ⭐ Leave reviews and ratings for tutors
- 💳 Secure payment processing
- 📊 Track learning progress and session history

### For Tutors
- 👨‍🏫 Create and customize tutor profiles
- 📋 Manage subject offerings and pricing
- 🗓️ Handle session scheduling and availability
- 💰 Track earnings and payment history
- 📈 Build reputation through student reviews

### Platform Features
- 🔐 User authentication and role-based access
- 📱 Responsive design for all devices
- 📊 Personalized dashboards for students and tutors
- 🔔 Real-time session notifications
- 🌐 Intuitive navigation and user-friendly interface

## 🛠️ Technologies

### Frontend
- **Framework**: React.js with TypeScript
- **Styling**: Tailwind CSS
- **Components**: Shadcn UI library
- **State Management**: React Query, React Context
- **Routing**: Wouter
- **Forms**: React Hook Form with Zod validation

### Backend
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: PostgreSQL
- **ORM**: Drizzle
- **Authentication**: Passport.js with session-based auth
- **Payments**: Stripe integration

## 📋 Prerequisites

- Node.js (v16+)
- PostgreSQL
- npm or yarn

## 🚀 Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/tadrees-marketplace.git
cd tadrees-marketplace
```

2. Install dependencies
```bash
npm install
```

3. Set up environment variables
```bash
cp .env.example .env
```
Edit the `.env` file with your database credentials and other configuration.

4. Set up the database
```bash
npm run db:push
```

5. Start the development server
```bash
npm run dev
```

## 📁 Project Structure

```
tadrees-marketplace/
├── client/              # Frontend code
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── lib/         # Utility functions
│   │   ├── pages/       # Page components
│   │   └── App.tsx      # Main app component
├── server/              # Backend code
│   ├── auth.ts          # Authentication logic
│   ├── index.ts         # Server entry point
│   ├── routes.ts        # API routes
│   ├── storage.ts       # Database operations
│   └── vite.ts          # Vite configuration
├── shared/              # Shared code
│   └── schema.ts        # Database schema and types
├── package.json         # Project dependencies
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## 📝 Usage

### Student Workflow
1. Create an account or log in
2. Browse tutors or use search filters to find a suitable tutor
3. View tutor profiles, ratings, and availability
4. Book a session with your chosen tutor
5. Make payment through the secure payment gateway
6. Attend the session at the scheduled time
7. Leave a review after the session

### Tutor Workflow
1. Create an account or log in
2. Complete your tutor profile with expertise and credentials
3. Set your availability and hourly rate
4. Receive booking requests from students
5. Manage upcoming sessions through your dashboard
6. Conduct tutoring sessions
7. Receive payments automatically after completed sessions

## 🔄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth` | POST | User authentication |
| `/api/tutors` | GET | Get list of tutors with filtering |
| `/api/tutors/:id` | GET | Get specific tutor details |
| `/api/bookings` | GET | Get user bookings |
| `/api/bookings` | POST | Create a new booking |
| `/api/user/become-tutor` | POST | Register as a tutor |
| `/api/sessions/:id` | GET | Get session details |
| `/api/create-payment-intent` | POST | Initialize payment process |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

SinaMohammadhHosseinZadeh - [your-email@example.com](mailto:your-email@example.com)

Project Link: [https://github.com/sinamohammadhosseinzadeh/tadrees-marketplace](https://github.com/sinamohammadhosseinzadeh/tadrees-marketplace)

---

## 🖼️ Screenshots

To add your own screenshots:

1. Navigate to your application in the browser (http://localhost:5173/)
2. Take screenshots of the following pages:
   - Home page
   - Tutors listing page
   - Tutor profile page
   - Dashboard
   - Booking page

3. Save the screenshots in the `public/screenshots` directory with these filenames:
   - `home-page.png`
   - `tutor-listing.png`
   - `tutor-profile.png`
   - `dashboard.png`
   - `booking-page.png`

4. The screenshots will automatically appear below:

<div align="center">
  <img src="public/screenshots/home-page.png" alt="Home Page" width="45%">
  <img src="public/screenshots/tutor-listing.png" alt="Tutor Listing" width="45%">
  <img src="public/screenshots/tutor-profile.png" alt="Tutor Profile" width="45%">
  <img src="public/screenshots/dashboard.png" alt="Dashboard" width="45%">
  <img src="public/screenshots/booking-page.png" alt="Booking Page" width="45%">
</div> 