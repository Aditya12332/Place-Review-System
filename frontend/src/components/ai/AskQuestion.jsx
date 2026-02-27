import React, { useState } from 'react';
import { Send, Sparkles, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';
import { aiService } from '../../services/aiService';
import Button from '../common/Button';
import toast from 'react-hot-toast';

const AskQuestion = ({ placeId }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const suggestedQuestions = [
    "Is this place good for families?",
    "What are the parking options?",
    "Is it wheelchair accessible?",
    "What's the price range?",
    "How's the service quality?",
  ];
  
  const handleAsk = async (q) => {
    const questionToAsk = q || question;
    if (!questionToAsk.trim()) {
      toast.error('Please enter a question');
      return;
    }
    
    setIsLoading(true);
    setAnswer(null);
    
    try {
      const data = await aiService.askQuestion(placeId, questionToAsk);
      setAnswer(data);
      setQuestion('');
    } catch (error) {
      toast.error('Failed to get answer');
    } finally {
      setIsLoading(false);
    }
  };
  
  const getConfidenceIcon = (confidence) => {
    if (confidence === 'high') return <CheckCircle className="text-success" />;
    if (confidence === 'medium') return <HelpCircle className="text-warning" />;
    return <AlertCircle className="text-error" />;
  };
  
  const getConfidenceColor = (confidence) => {
    if (confidence === 'high') return 'badge-success';
    if (confidence === 'medium') return 'badge-warning';
    return 'badge-error';
  };
  
  return (
    <div className="card bg-base-100 border border-base-content/10 shadow-lg">
      <div className="card-body">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="text-primary" size={24} />
          <h3 className="text-xl font-bold">Ask AI About This Place</h3>
        </div>
        
        {/* Question Input */}
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
            placeholder="Ask anything about this place..."
            className="input input-bordered flex-1"
            disabled={isLoading}
          />
          <Button
            onClick={() => handleAsk()}
            isLoading={isLoading}
            disabled={!question.trim()}
          >
            <Send size={20} />
          </Button>
        </div>
        
        {/* Suggested Questions */}
        <div className="mb-4">
          <p className="text-sm text-base-content/70 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, index) => (
              <button
                key={index}
                onClick={() => handleAsk(q)}
                disabled={isLoading}
                className="btn btn-sm btn-outline"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        
        {/* Answer */}
        {answer && (
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-6 animate-slide-up">
            <div className="flex items-start justify-between mb-4">
              <h4 className="font-semibold text-lg">{answer.question}</h4>
              <div className="flex items-center gap-2">
                {getConfidenceIcon(answer.confidence)}
                <span className={`badge ${getConfidenceColor(answer.confidence)}`}>
                  {answer.confidence} confidence
                </span>
              </div>
            </div>
            
            <p className="text-base-content/90 mb-4 leading-relaxed">
              {answer.answer}
            </p>
            
            {answer.sources.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-base-content/70 mb-2">
                  Based on these reviews:
                </p>
                <div className="space-y-2">
                  {answer.sources.map((source, index) => (
                    <div
                      key={index}
                      className="bg-base-100 rounded p-3 text-sm text-base-content/70 italic border-l-4 border-primary"
                    >
                      "{source}"
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AskQuestion;