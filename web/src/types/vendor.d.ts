declare module '@toast-ui/editor' {
  export interface EditorOptions {
    el: HTMLElement
    height?: string
    initialEditType?: 'markdown' | 'wysiwyg'
    initialValue?: string
    previewStyle?: 'vertical' | 'tab'
    usageStatistics?: boolean
    hideModeSwitch?: boolean
    placeholder?: string
    events?: {
      change?: () => void
    }
  }

  export default class Editor {
    constructor(options: EditorOptions)
    destroy(): void
    getHTML(): string
    getMarkdown(): string
    setHTML(value: string): void
    setMarkdown(value: string, cursorToEnd?: boolean): void
    changeMode(mode: 'markdown' | 'wysiwyg', withoutFocus?: boolean): void
  }
}

declare module 'markdown-it' {
  export default class MarkdownIt {
    constructor(options?: Record<string, unknown>)
    render(markdown: string): string
  }
}
