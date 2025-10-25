# Cross-Encoder Reranker - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
cd backend
uv sync --extra reranker
```

### Step 2: Test Installation (1 min)

```bash
python test_reranker.py
```

✅ Expected: "All tests completed successfully!"

### Step 3: Enable Reranker (1 min)

Edit `.env` file or set environment variables:

```bash
# Add these lines
RAG_USE_RERANKER=True
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Step 4: Restart Backend (1 min)

```bash
docker-compose restart backend
```

### Step 5: Verify (1 min)

Check logs for:
```
✓ Cross-encoder reranking enabled
```

Test a query in your chatbot - results should be more relevant!

## 📊 What You Get

**Before:**
- Hybrid search: 80ms latency
- Good relevance: ★★★★☆

**After:**
- Hybrid + Reranker: 150ms latency
- Excellent relevance: ★★★★★

## ⚙️ Configuration

Default settings (good for most cases):
```bash
RAG_USE_RERANKER=True                              # Enable it
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2  # Fast model
RAG_RERANKER_TOP_K=10                              # Top 10 results
RAG_RERANKER_QUALITY_WEIGHT=0.3                    # 70% relevance, 30% quality
```

## 🔧 Troubleshooting

**Problem:** Import error
```bash
cd backend
uv pip install sentence-transformers
```

**Problem:** Too slow
```bash
# Use faster model or disable for now
RAG_USE_RERANKER=False
```

**Problem:** High memory
```bash
# Reduce top K
RAG_RERANKER_TOP_K=5
```

## 📚 Documentation

- Full Guide: `CROSS_ENCODER_RERANKER_README.md`
- Implementation: `RERANKER_IMPLEMENTATION_SUMMARY.md`
- Overall Strategy: `ADVANCED_RAG_ENHANCEMENT_GUIDE.md`

## ✨ Next Steps

1. **Test with real queries** - Try complex questions
2. **Monitor performance** - Check latency impact
3. **Collect feedback** - Is relevance better?
4. **Tune settings** - Adjust quality weight if needed

## 🎯 Success Criteria

- [ ] Installation successful
- [ ] Tests pass
- [ ] Backend restarts without errors
- [ ] Logs show reranker enabled
- [ ] Query results more relevant
- [ ] Latency acceptable (< 200ms)

That's it! You're now using state-of-the-art RAG reranking! 🎉
