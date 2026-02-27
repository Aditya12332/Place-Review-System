export const validatePhoneNumber = (phone) => {
  const phoneRegex = /^\+?1?\d{9,15}$/;
  return phoneRegex.test(phone);
};

export const validatePassword = (password) => {
  return password.length >= 6;
};

export const validateRating = (rating) => {
  return rating >= 1 && rating <= 5;
};

export const validateRequired = (value) => {
  return value && value.toString().trim().length > 0;
};

export const sanitizeInput = (input) => {
  return input.trim().replace(/[<>]/g, '');
};