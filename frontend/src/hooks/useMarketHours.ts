import { useState, useEffect } from 'react';

export function useMarketHours() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const check = () => {
      // IST = UTC + 5:30
      const now = new Date();
      const utc = now.getTime() + now.getTimezoneOffset() * 60000;
      const ist = new Date(utc + 5.5 * 3600000);
      const h = ist.getHours();
      const m = ist.getMinutes();
      const open =
        (h === 9 && m >= 15) ||
        (h > 9 && h < 15) ||
        (h === 15 && m <= 30);
      setIsOpen(open);
    };
    check();
    const id = setInterval(check, 60000);
    return () => clearInterval(id);
  }, []);

  return isOpen;
}
