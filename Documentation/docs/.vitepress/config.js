export default {
  base: '/',  // Use '/' for Vercel, '/repo-name/' for GitHub Pages
  title: 'Team Robomanipal',
  description: 'Hardware Hackathon 3.0 Documentation',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Dashboard', link: '/dashboard/index.html', target: '_self' }
    ],
    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'Market Research', link: '/research/market-research' },
          { text: 'Case Study', link: '/research/case-study' }
        ]
      },
      {
        text: 'Hardware Architecture',
        items: [
          { text: 'Mechanical Design', link: '/hardware/mechanical' },
          { text: 'Electronics & Schematics', link: '/hardware/electronics' },
          { text: 'Bill of Materials', link: '/hardware/bom' }
        ]
      },
      {
        text: 'Software & Firmware',
        items: [
          { text: 'Setup & Installation', link: '/software/setup' },
          { text: 'Code Structure', link: '/software/code' },
          { text: 'Communication Protocols', link: '/software/protocols' }
        ]
      },
      {
        text: 'Testing & Results',
        items: [
          { text: 'Methodology', link: '/results/methodology' },
          { text: 'Discussion', link: '/results/discussion' }
        ]
      }
    ]
  }
}
