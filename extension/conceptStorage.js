window.ConceptStorage = {
  async getConcepts() {
    const result = await chrome.storage.local.get("concepts");

    if (Array.isArray(result.concepts)) {
      return result.concepts;
    }

    return [];
  },

  async saveConcepts(concepts) {
    await chrome.storage.local.set({ concepts });
  },

  async initializeConcepts(defaultConcepts) {
    const result = await chrome.storage.local.get("concepts");

    // Only seed defaults if the key has never been created.
    if (Array.isArray(result.concepts)) {
      return result.concepts;
    }

    await chrome.storage.local.set({
      concepts: defaultConcepts
    });

    return defaultConcepts;
  }
};