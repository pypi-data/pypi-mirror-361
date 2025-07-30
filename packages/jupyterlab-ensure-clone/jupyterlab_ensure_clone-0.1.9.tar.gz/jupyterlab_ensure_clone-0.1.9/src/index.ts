/* eslint "no-constant-condition": "off" */

import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { showDialog } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { requestAPI } from './handler';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-ensure-clone:plugin',
  description: 'Ensure a git repo is cloned on startup.',
  autoStart: true,
  requires: [ISettingRegistry],
  activate: async (app: JupyterFrontEnd, settingsRegistry: ISettingRegistry) => {
    console.log(`JupyterLab extension ${plugin.id} is activated!`);
    const settings = (await settingsRegistry.load(plugin.id)).composite.private as any;
    window.setTimeout(() => ensureClone(settings), 2000);
  }
};

async function ensureClone(settings: any) {
  const form = new LoginForm(settings);
  let input = settings as any;
  let errCount = 0;
  while (true) {
    try {
      await requestAPI<any>('', { method: 'POST', body: JSON.stringify(input) });
      break;
    } catch (err) {
      errCount++;
      // If we're missing credentials and the repo requires them, an initial error is expected.
      const title = errCount < 2 ? settings.title : 'Error ensuring clone, try again?';
      while (true) {
        input = await showDialog({ title: title, body: form });
        if (!input.button.accept) {
          if (confirm('You may be missing functionality if you cancel. Are you sure?')) {
            return;
          }
          continue;
        }
        break;
      }
      input = input.value;
      input.repoUrl = input.repoUrl || settings.repoUrl;
      input.targetDir = input.targetDir || settings.targetDir;
    }
  }
}

class LoginForm extends Widget {
  private repoUrlInput: HTMLInputElement;
  private targetDirInput: HTMLInputElement;
  private usernameInput: HTMLInputElement;
  private passwordInput: HTMLInputElement;

  constructor(settings: any) {
    super();
    this.addClass('jp-LoginForm');
    if (settings.helpText) {
      this.node.appendChild(document.createElement('p')).textContent = settings.helpText;
    }
    this.repoUrlInput = this.createInput({ placeholder: 'Repo URL' });
    this.targetDirInput = this.createInput({ placeholder: 'Target directory' });
    this.usernameInput = this.createInput({ placeholder: 'Username' });
    this.passwordInput = this.createInput({ placeholder: 'Password', type: 'password' });
    if (!settings.repoUrl) {
      this.node.appendChild(this.repoUrlInput);
    }
    if (!settings.targetDir) {
      this.node.appendChild(this.targetDirInput);
    }
    if (settings.needCredentials) {
      this.node.appendChild(this.usernameInput);
      this.node.appendChild(this.passwordInput);
    }
  }

  createInput({ placeholder = '', type = 'text' }): HTMLInputElement {
    const input = document.createElement('input');
    input.placeholder = placeholder;
    input.type = type;
    input.className = 'jp-mod-styled jp-Input';
    input.style.marginBottom = '10px';
    return input;
  }

  getValue(): { repoUrl: string; targetDir: string; username: string; password: string } {
    return {
      repoUrl: this.repoUrlInput.value,
      targetDir: this.targetDirInput.value,
      username: this.usernameInput.value,
      password: this.passwordInput.value
    };
  }
}

export default plugin;
