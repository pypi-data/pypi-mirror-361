import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { MainAreaWidget } from '@jupyterlab/apputils';
import { FileManagerPanelWidget } from './widgets/FileManagerPanelWidget';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { registerLicense } from '@syncfusion/ej2-base';
import { ILabShell } from '@jupyterlab/application';
import { requestAPI } from './handler';
import { telescopeIcon } from './style/IconsStyle';

interface ConfigResponse {
  LICENSE: string;
  CHATLAS: string;
}

const config = await requestAPI<ConfigResponse>('config', {
  method: 'GET'
});

registerLicense(config.LICENSE);

const PLUGIN_ID = 'jupyterlab-bxplorer:plugin';

async function activate(
  app: JupyterFrontEnd,
  settingRegistry: ISettingRegistry
): Promise<void> {
  console.log('JupyterLab extension jupyterlab-bxplorer is activated!');

  let downloadsFolder = '';
  const atlasId = config.CHATLAS;
  if (settingRegistry) {
    await settingRegistry
      .load(plugin.id)
      .then(settings => {
        downloadsFolder =
          (settings.get('download-folder').composite as string) || '';
      })
      .catch(reason => {
        console.error(
          'Failed to load settings for jupyterlab-bxplorer.',
          reason
        );
      });
  }

  const leftSideBarContent = new FileManagerPanelWidget(
    downloadsFolder,
    atlasId
  );
  const leftSideBarWidget = new MainAreaWidget<FileManagerPanelWidget>({
    content: leftSideBarContent
  });
  leftSideBarWidget.id = 'filemanager-panel-widget';
  leftSideBarWidget.toolbar.hide();
  leftSideBarWidget.title.icon = telescopeIcon;
  leftSideBarWidget.title.caption = 'File Manager';
  app.shell.add(leftSideBarWidget, 'left', { rank: 501 });

  const shell = app.shell as ILabShell;
  if (shell.leftCollapsed) {
    shell.expandLeft();
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description: 'A JupyterLab extension.',
  autoStart: true,
  optional: [ISettingRegistry],
  activate
};

export default plugin;
