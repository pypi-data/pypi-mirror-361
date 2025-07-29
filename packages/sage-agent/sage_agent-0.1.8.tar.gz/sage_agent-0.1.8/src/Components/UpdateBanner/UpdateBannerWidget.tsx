import * as React from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { ListModel } from '@jupyterlab/extensionmanager';

/**
 * Interface for the UpdateBanner state
 */
interface IUpdateBannerState {
  isVisible: boolean;
  currentVersion?: string;
  latestVersion?: string;
  isUpdating: boolean;
  isDeclined: boolean;
}

/**
 * React component for displaying update banner content
 */
interface UpdateBannerContentProps {
  isVisible: boolean;
  currentVersion?: string;
  latestVersion?: string;
  isUpdating: boolean;
  onUpdate: () => void;
  onAskLater: () => void;
  onDecline: () => void;
}

function UpdateBannerContent({
  isVisible,
  currentVersion,
  latestVersion,
  isUpdating,
  onUpdate,
  onAskLater,
  onDecline
}: UpdateBannerContentProps): JSX.Element | null {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="sage-ai-update-banner">
      <div className="sage-ai-update-banner-content">
        <div className="sage-ai-update-banner-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div className="sage-ai-update-banner-text">
          <div className="sage-ai-update-banner-title">
            Sage needs to update
          </div>
          {currentVersion && latestVersion && (
            <div className="sage-ai-update-banner-version">
              v{currentVersion} → v{latestVersion}
            </div>
          )}
        </div>
        <div className="sage-ai-update-banner-actions">
          <button
            className="sage-ai-update-banner-button sage-ai-update-banner-button-update"
            onClick={onUpdate}
            disabled={isUpdating}
          >
            {isUpdating ? 'Updating...' : 'Update'}
          </button>
          <button
            className="sage-ai-update-banner-button sage-ai-update-banner-button-later"
            onClick={onAskLater}
            disabled={isUpdating}
          >
            Ask Me Later
          </button>
          <button
            className="sage-ai-update-banner-button sage-ai-update-banner-button-decline"
            onClick={onDecline}
            disabled={isUpdating}
          >
            Decline
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Component for displaying update banner above the chatbox
 */
export class UpdateBannerWidget extends ReactWidget {
  private _state: IUpdateBannerState;
  private _stateChanged = new Signal<this, IUpdateBannerState>(this);
  private _extensions: ListModel;
  private _packageName: string = 'sage-agent';
  private _checkInterval: number | null = null;

  constructor(extensions: ListModel) {
    super();
    this._extensions = extensions;
    this._state = {
      isVisible: false,
      isUpdating: false,
      isDeclined: this.getDeclinedStatus()
    };
    this.addClass('sage-ai-update-banner-widget');

    // Initially hide the widget
    this.node.style.display = 'none';

    this.checkForUpdates();
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, IUpdateBannerState> {
    return this._stateChanged;
  }

  /**
   * Check if updates have been declined permanently
   */
  private getDeclinedStatus(): boolean {
    try {
      return localStorage.getItem('sage-agent-update-declined') === 'true';
    } catch {
      return false;
    }
  }

  /**
   * Set declined status in localStorage
   */
  private setDeclinedStatus(declined: boolean): void {
    try {
      if (declined) {
        localStorage.setItem('sage-agent-update-declined', 'true');
      } else {
        localStorage.removeItem('sage-agent-update-declined');
      }
    } catch {
      // Ignore localStorage errors
    }
  }

  /**
   * Check for updates and show banner if needed
   */
  public async checkForUpdates(): Promise<void> {
    try {
      console.log('CHECKING FOR UPDATES...');
      console.log(`Current state: ${JSON.stringify(this._state)}`);
      // Don't check if user has declined updates
      if (this._state.isDeclined) {
        return;
      }

      await this._extensions.refreshInstalled(true);
      const installed = this._extensions.installed.find(
        value => value.name === this._packageName
      );

      if (
        installed &&
        installed.installed_version !== installed.latest_version
      ) {
        this._state = {
          ...this._state,
          isVisible: true,
          currentVersion: installed.installed_version,
          latestVersion: installed.latest_version
        };
        this._stateChanged.emit(this._state);
        this.updateDisplayState();
        this.update();
      }
    } catch (error) {
      console.error('Failed to check for updates:', error);
    }
  }

  /**
   * Update the widget's display state based on visibility
   */
  private updateDisplayState(): void {
    this.node.style.display = this._state.isVisible ? 'block' : 'none';
  }

  /**
   * Handle update button click
   */
  private handleUpdate = async (): Promise<void> => {
    this._state = { ...this._state, isUpdating: true };
    this._stateChanged.emit(this._state);
    this.update();

    try {
      const installed = this._extensions.installed.find(
        value => value.name === this._packageName
      );

      if (installed) {
        console.log(
          `Updating ${this._packageName} to version ${installed.latest_version}`
        );

        // Perform the actual update
        await this._extensions.install(installed, {
          useVersion: installed.latest_version
        });

        // Hide the banner after successful update
        this._state = {
          ...this._state,
          isVisible: false,
          isUpdating: false
        };
        this._stateChanged.emit(this._state);
        this.updateDisplayState();
        this.update();

        console.log(
          `Successfully updated ${this._packageName} to version ${installed.latest_version}`
        );
      }
    } catch (error) {
      console.error('Failed to update:', error);
      this._state = { ...this._state, isUpdating: false };
      this._stateChanged.emit(this._state);
      this.updateDisplayState();
      this.update();
    }
  };

  /**
   * Handle ask me later button click
   */
  private handleAskLater = (): void => {
    this._state = { ...this._state, isVisible: false };
    this._stateChanged.emit(this._state);
    this.updateDisplayState();
    this.update();
  };

  /**
   * Handle decline button click
   */
  private handleDecline = (): void => {
    this.setDeclinedStatus(true);
    this._state = {
      ...this._state,
      isVisible: false,
      isDeclined: true
    };
    this._stateChanged.emit(this._state);
    this.updateDisplayState();
    this.update();
  };

  /**
   * Show the banner (e.g., after app launch)
   */
  public showBanner(): void {
    if (!this._state.isDeclined) {
      this.checkForUpdates();
    }
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <UpdateBannerContent
        isVisible={this._state.isVisible}
        currentVersion={this._state.currentVersion}
        latestVersion={this._state.latestVersion}
        isUpdating={this._state.isUpdating}
        onUpdate={this.handleUpdate}
        onAskLater={this.handleAskLater}
        onDecline={this.handleDecline}
      />
    );
  }

  /**
   * Dispose of the widget
   */
  dispose(): void {
    if (this._checkInterval) {
      clearInterval(this._checkInterval);
      this._checkInterval = null;
    }
    super.dispose();
  }
}
