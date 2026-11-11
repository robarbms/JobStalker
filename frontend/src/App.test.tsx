import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';
import { dateToString } from './utils/date';

jest.mock('./components/admin_panel/admin_panel', () => ({
  __esModule: true,
  default: ({ open }: { open: boolean }) => open ? <div>Scraper administration</div> : null,
}));

test('opens scraper administration from the accessible settings button', async () => {
  const originalFetch = global.fetch;
  global.fetch = jest.fn().mockResolvedValue({ json: async () => [{
    id: 1, job_id: 'qa', title: 'QA Engineer', company: 'Reddit',
    date_posted: dateToString(new Date()), created_at: new Date().toISOString(),
    link: 'https://example.com', tags: '[]', salary_min: 0, salary_max: 0,
    summary: 'Offline test fixture',
  }] });
  render(<App />);
  await screen.findByText('QA Engineer');
  fireEvent.click(screen.getByRole('button', { name: 'Open Admin Panel' }));
  expect(await screen.findByText('Scraper administration')).toBeInTheDocument();
  global.fetch = originalFetch;
});
