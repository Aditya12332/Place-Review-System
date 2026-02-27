import { Toaster } from 'react-hot-toast';

const Toast = () => {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: 'hsl(var(--b1))',
          color: 'hsl(var(--bc))',
          border: '1px solid hsl(var(--bc) / 0.1)',
        },
        success: {
          iconTheme: {
            primary: 'hsl(var(--su))',
            secondary: 'hsl(var(--b1))',
          },
        },
        error: {
          iconTheme: {
            primary: 'hsl(var(--er))',
            secondary: 'hsl(var(--b1))',
          },
        },
      }}
    />
  );
};

export default Toast;