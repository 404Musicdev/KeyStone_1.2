# Learn to Read & Spelling UI Components

## Components to Add to StudentDashboard.js

### 1. Learn to Read Handler Functions (Add after existing handlers)

```javascript
const handleWordClick = (activityIndex, word) => {
  setInteractiveWordAnswers(prev => ({
    ...prev,
    [activityIndex]: word
  }));
};

const speak Text = (text) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.8; // Slower for learning
    window.speechSynthesis.speak(utterance);
  }
};
```

### 2. Spelling Handler Functions (Add after Learn to Read handlers)

```javascript
const handleSpellingAnswer = (exerciseIndex, answer) => {
  setSpellingAnswers(prev => ({
    ...prev,
    [exerciseIndex]: answer
  }));
};
```

### 3. Update handleSubmit validation (Replace existing)

Add validation for Learn to Read and Spelling before submission.

### 4. Learn to Read UI Section (Add after drag-drop section, before submit button)

Full UI with TTS buttons, clickable words, and interactive activities.

### 5. Spelling UI Section (Add after Learn to Read section)

Three types of exercises: typing test, fill-in-blank, multiple choice with TTS audio.

## Full code in separate implementation file for token efficiency.
