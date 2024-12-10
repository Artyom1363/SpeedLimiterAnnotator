import React from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  Typography 
} from '@mui/material';

interface ThankYouModalProps {
  open: boolean;
  onClose: () => void;
  onNextVideo: () => void;
}

const ThankYouModal: React.FC<ThankYouModalProps> = ({ open, onClose, onNextVideo }) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Спасибо за разметку!</DialogTitle>
      <DialogContent>
        <Typography>
          Ваша работа помогает улучшить точность определения скорости электросамокатов.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Закрыть
        </Button>
        <Button onClick={onNextVideo} variant="contained" color="primary">
          Перейти к следующему видео
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ThankYouModal;
