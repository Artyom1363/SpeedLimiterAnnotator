import React from 'react';
import { Box, Container } from '@mui/material';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        {children}
      </Box>
    </Container>
  );
};

export default Layout;